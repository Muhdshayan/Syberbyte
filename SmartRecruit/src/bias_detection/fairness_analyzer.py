import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re

class FairnessAnalyzer:
    def __init__(self, settings):
        self.settings = settings
        self.demographic_patterns = self._load_demographic_patterns()
        self.tracking_data = []
    
    def _load_demographic_patterns(self) -> Dict:
        """Load patterns for demographic detection"""
        return {
            'gender': {
                'male_indicators': ['he/him', 'his', 'mr.', 'father', 'son'],
                'female_indicators': ['she/her', 'hers', 'ms.', 'mrs.', 'mother', 'daughter'],
                'neutral_indicators': ['they/them', 'their']
            },
            'age': {
                'patterns': [
                    r'\b(\d{4})\s*-\s*(\d{4})\b',  # Year ranges
                    r'(\d+)\s*years?\s*experience',
                    r'graduated\s*(\d{4})'
                ]
            }
        }
    
    async def analyze_candidate_pool(self, candidates: List[Dict], 
                                   job_description: Dict) -> Dict:
        """Analyze fairness across candidate pool"""
        # Extract demographic data
        demographics = self._extract_demographics(candidates)
        
        # Calculate selection rates
        selection_rates = self._calculate_selection_rates(
            candidates, demographics
        )
        
        # Perform statistical tests
        bias_tests = self._perform_bias_tests(selection_rates)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            bias_tests, selection_rates
        )
        
        # Create visualizations
        visualizations = self._create_fairness_visualizations(
            selection_rates, demographics
        )
        
        # Track for longitudinal analysis
        self._track_hiring_decision(candidates, job_description, demographics)
        
        return {
            'demographics': demographics,
            'selection_rates': selection_rates,
            'bias_tests': bias_tests,
            'recommendations': recommendations,
            'visualizations': visualizations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_demographics(self, candidates: List[Dict]) -> pd.DataFrame:
        """Extract demographic information from candidates"""
        data = []
        
        for candidate in candidates:
            profile = candidate['candidate']['data']['profile']
            
            demographics = {
                'candidate_id': candidate['candidate']['id'],
                'score': candidate['total_score'],
                'selected': candidate['total_score'] >= 80,  # Threshold
            }
            
            # Infer gender (carefully, with limitations noted)
            demographics['gender'] = self._infer_gender(profile)
            
            # Estimate age range
            demographics['age_range'] = self._estimate_age_range(profile)
            
            # Extract other relevant factors
            demographics['education_type'] = self._categorize_education(profile)
            
            data.append(demographics)
        
        return pd.DataFrame(data)
    
    def _infer_gender(self, profile: Dict) -> str:
        """Carefully infer gender with 'unknown' default"""
        # This is a sensitive area - in production, consider:
        # 1. Asking candidates directly (with 'prefer not to say' option)
        # 2. Not inferring at all
        # 3. Using this only for aggregate bias detection
        
        name = profile.get('name', '').lower()
        
        # Check pronouns first (most reliable if provided)
        contact_text = str(profile.get('contact', {}))
        for pattern in self.demographic_patterns['gender']['male_indicators']:
            if pattern in contact_text.lower():
                return 'male'
        for pattern in self.demographic_patterns['gender']['female_indicators']:
            if pattern in contact_text.lower():
                return 'female'
        
        return 'unknown'
    
    def _estimate_age_range(self, profile: Dict) -> str:
        """Estimate age range from education/experience dates"""
        # Find graduation year
        education = profile.get('education', [])
        grad_year = None
        
        for edu in education:
            year_match = re.search(r'(\d{4})', edu.get('year', ''))
            if year_match:
                grad_year = int(year_match.group(1))
                break
        
        if grad_year:
            years_since_grad = 2025 - grad_year
            
            if years_since_grad < 5:
                return '20-25'
            elif years_since_grad < 10:
                return '25-30'
            elif years_since_grad < 15:
                return '30-35'
            elif years_since_grad < 20:
                return '35-40'
            else:
                return '40+'
        
        return 'unknown'
    
    def _categorize_education(self, profile: Dict) -> str:
        """Categorize education background"""
        education = profile.get('education', [])
        
        for edu in education:
            institution = edu.get('institution', '').lower()
            if 'university' in institution:
                if any(elite in institution for elite in ['mit', 'stanford', 'harvard']):
                    return 'elite_university'
                return 'university'
            elif 'college' in institution:
                return 'college'
        
        return 'other'
    
    def _calculate_selection_rates(self, candidates: List[Dict], 
                                 demographics: pd.DataFrame) -> Dict:
        """Calculate selection rates by demographic groups"""
        rates = {}
        
        # Overall selection rate
        overall_rate = demographics['selected'].mean()
        rates['overall'] = overall_rate
        
        # By demographic categories
        for category in ['gender', 'age_range', 'education_type']:
            rates[category] = {}
            
            for group in demographics[category].unique():
                if group != 'unknown':
                    group_data = demographics[demographics[category] == group]
                    if len(group_data) > 0:
                        rates[category][group] = {
                            'selection_rate': group_data['selected'].mean(),
                            'count': len(group_data),
                            'avg_score': group_data['score'].mean()
                        }
        
        return rates
    
    def _perform_bias_tests(self, selection_rates: Dict) -> Dict:
        """Perform statistical tests for bias"""
        tests = {}
        
        overall_rate = selection_rates['overall']
        
        for category, groups in selection_rates.items():
            if category == 'overall':
                continue
            
            tests[category] = {}
            
            # Four-fifths rule
            for group, stats in groups.items():
                group_rate = stats['selection_rate']
                
                # Check if selection rate is substantially lower
                if overall_rate > 0:
                    impact_ratio = group_rate / overall_rate
                    tests[category][group] = {
                        'impact_ratio': impact_ratio,
                        'four_fifths_rule': impact_ratio >= 0.8,
                        'sample_size': stats['count']
                    }
            
            # Chi-square test for independence
            if len(groups) > 1:
                observed = []
                expected = []
                
                for group, stats in groups.items():
                    selected = int(stats['selection_rate'] * stats['count'])
                    not_selected = stats['count'] - selected
                    observed.extend([selected, not_selected])
                    
                    expected_selected = overall_rate * stats['count']
                    expected_not_selected = (1 - overall_rate) * stats['count']
                    expected.extend([expected_selected, expected_not_selected])
                
                if all(e > 5 for e in expected):  # Chi-square validity
                    chi2, p_value = stats.chisquare(observed, expected)
                    tests[category]['chi_square'] = {
                        'statistic': chi2,
                        'p_value': p_value,
                        'significant': p_value < 0.05
                    }
        
        return tests
    
    def _generate_recommendations(self, bias_tests: Dict, 
                                selection_rates: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for category, tests in bias_tests.items():
            # Check for failing four-fifths rule
            failing_groups = [
                group for group, test in tests.items()
                if isinstance(test, dict) and 
                'four_fifths_rule' in test and 
                not test['four_fifths_rule']
            ]
            
            if failing_groups:
                recommendations.append({
                    'category': category,
                    'severity': 'high',
                    'issue': f"Selection rate disparity in {category}",
                    'affected_groups': failing_groups,
                    'action': f"Review scoring criteria that may disadvantage {', '.join(failing_groups)}",
                    'suggestion': "Consider blind resume screening or adjusted scoring weights"
                })
            
            # Check for statistical significance
            if 'chi_square' in tests and tests['chi_square']['significant']:
                recommendations.append({
                    'category': category,
                    'severity': 'medium',
                    'issue': f"Statistically significant bias detected in {category}",
                    'action': "Investigate systematic factors affecting selection",
                    'suggestion': "Implement structured interviews and standardized evaluation"
                })
        
        # Check sample sizes
        for category, groups in selection_rates.items():
            if category == 'overall':
                continue
            
            small_samples = [
                group for group, stats in groups.items()
                if isinstance(stats, dict) and stats.get('count', 0) < 10
            ]
            
            if small_samples:
                recommendations.append({
                    'category': category,
                    'severity': 'low',
                    'issue': f"Small sample size for {', '.join(small_samples)}",
                    'action': "Increase candidate pool diversity",
                    'suggestion': "Expand sourcing channels and partnerships"
                })
        
        return recommendations
    
    def _create_fairness_visualizations(self, selection_rates: Dict, 
                                      demographics: pd.DataFrame) -> Dict:
        """Create interactive visualizations"""
        visualizations = {}
        
        # Selection rate comparison
        fig_rates = go.Figure()
        
        for category, groups in selection_rates.items():
            if category == 'overall':
                continue
            
            x_values = []
            y_values = []
            text_values = []
            
            for group, stats in groups.items():
                if isinstance(stats, dict):
                    x_values.append(f"{category}: {group}")
                    y_values.append(stats['selection_rate'] * 100)
                    text_values.append(f"n={stats['count']}")
            
            fig_rates.add_trace(go.Bar(
                x=x_values,
                y=y_values,
                text=text_values,
                textposition='auto',
                name=category
            ))
        
        fig_rates.update_layout(
            title="Selection Rates by Demographic Group",
            xaxis_title="Group",
            yaxis_title="Selection Rate (%)",
            showlegend=True
        )
        
        # Add reference line for overall rate
        fig_rates.add_hline(
            y=selection_rates['overall'] * 100,
            line_dash="dash",
            annotation_text="Overall Rate"
        )
        
        visualizations['selection_rates'] = fig_rates.to_json()
        
        # Score distribution
        fig_dist = px.box(
            demographics,
            x='gender',
            y='score',
            color='selected',
            title="Score Distribution by Gender",
            labels={'score': 'Match Score', 'selected': 'Selected'}
        )
        
        visualizations['score_distribution'] = fig_dist.to_json()
        
        # Intersectional analysis
        pivot_data = demographics.pivot_table(
            values='selected',
            index='age_range',
            columns='gender',
            aggfunc='mean'
        )
        
        fig_intersect = go.Figure(data=go.Heatmap(
            z=pivot_data.values * 100,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='RdYlGn',
            text=np.round(pivot_data.values * 100, 1),
            texttemplate='%{text}%',
            textfont={"size": 12}
        ))
        
        fig_intersect.update_layout(
            title="Intersectional Selection Rates (%)",
            xaxis_title="Gender",
            yaxis_title="Age Range"
        )
        
        visualizations['intersectional'] = fig_intersect.to_json()
        
        return visualizations
    
    def _track_hiring_decision(self, candidates: List[Dict], 
                             job_description: Dict, 
                             demographics: pd.DataFrame):
        """Track decisions for longitudinal analysis"""
        tracking_entry = {
            'timestamp': datetime.now(),
            'job_id': hash(str(job_description)),
            'job_title': job_description.get('title'),
            'candidate_count': len(candidates),
            'demographics_summary': {
                'gender_distribution': demographics['gender'].value_counts().to_dict(),
                'age_distribution': demographics['age_range'].value_counts().to_dict(),
                'selection_rates': {
                    'overall': demographics['selected'].mean(),
                    'by_gender': demographics.groupby('gender')['selected'].mean().to_dict()
                }
            }
        }
        
        self.tracking_data.append(tracking_entry)
        
        # Persist tracking data (implement based on your storage choice)
        self._save_tracking_data()
    
    def _save_tracking_data(self):
        """Save tracking data for historical analysis"""
        # Implement persistence logic
        pass
    
    def generate_fairness_report(self) -> Dict:
        """Generate comprehensive fairness report"""
        if not self.tracking_data:
            return {"error": "No tracking data available"}
        
        df = pd.DataFrame(self.tracking_data)
        
        report = {
            'summary': {
                'total_jobs_analyzed': len(df),
                'total_candidates_reviewed': df['candidate_count'].sum(),
                'date_range': {
                    'start': df['timestamp'].min().isoformat(),
                    'end': df['timestamp'].max().isoformat()
                }
            },
            'trends': self._analyze_trends(df),
            'recommendations': self._generate_system_recommendations(df)
        }
        
        return report
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze trends over time"""
        # Implement trend analysis
        return {
            'selection_rate_trend': 'stable',
            'diversity_trend': 'improving',
            'bias_incidents': []
        }
    
    def _generate_system_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate system-wide recommendations"""
        return [
            "Implement regular bias audits",
            "Diversify sourcing channels",
            "Standardize interview processes",
            "Train hiring managers on unconscious bias"
        ]