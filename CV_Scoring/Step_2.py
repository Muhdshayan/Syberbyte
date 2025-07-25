import json
import os
from datetime import datetime

def convert_resume_format(resume_data):
    """
    Convert resume data from parsed format to standardized candidate format
    """
    converted_candidates = []
    
    for candidate in resume_data:
        # Extract basic information
        name = candidate.get('name', '')
        email = candidate.get('email', '')
        
        # Handle education - support both single and multiple degrees
        education_data = candidate.get('education', {})
        if isinstance(education_data.get('degree'), list):
            # Multiple degrees - take the most recent/highest
            degrees = education_data.get('degree', [])
            years = education_data.get('year', [])
            # Take the first degree (usually highest/most recent)
            degree = degrees[0] if degrees else ''
            year = years[0] if years else ''
        else:
            # Single degree
            degree = education_data.get('degree', '')
            year = education_data.get('year', '')
        
        # Extract field from degree name
        field = extract_field_from_degree(degree)
        
        # Determine degree level
        degree_level = determine_degree_level(degree)
        
        # Clean year (extract just the year number)
        clean_year = extract_year(year)
        
        # Convert experience
        years_exp = candidate.get('years_of_experience', 0)
        years = int(years_exp)
        months = int((years_exp % 1) * 12)
        
        # Generate a job title based on skills and experience
        job_title = generate_job_title(candidate.get('skills', {}), years_exp)
        
        # Convert skills to the target format
        skills = convert_skills(candidate.get('skills', {}))
        
        # Create the converted candidate object
        converted_candidate = {
            "name": name,
            "email": email,
            "Education": {
                "degree": degree_level,
                "year": str(clean_year),
                "field": field
            },
            "Experience": {
                "Years": str(years),
                "Months": str(months),
                "Title": job_title
            },
            "Skills": skills
        }
        
        converted_candidates.append(converted_candidate)
    
    return converted_candidates

def extract_field_from_degree(degree):
    """Extract field of study from degree name"""
    if not degree:
        return "Not specified"
    
    degree_lower = degree.lower()
    
    # Map degree names to fields
    field_mappings = {
        'computer science': 'Computer Science',
        'software engineering': 'Software Engineering',
        'biotechnology': 'Biotechnology',
        'business analytics': 'Business Analytics',
        'commerce': 'Commerce',
        'project management': 'Project Management',
        'international relations': 'International Relations'
    }
    
    for key, value in field_mappings.items():
        if key in degree_lower:
            return value
    
    # If no mapping found, clean up the degree name
    if 'bs' in degree_lower or 'bachelor' in degree_lower:
        field = degree.replace('BS', '').replace('Bachelor', '').replace('of', '').strip()
        return field.title() if field else "Not specified"
    
    return degree.strip()

def determine_degree_level(degree):
    """Determine if degree is Bachelor's or Master's"""
    if not degree:
        return "Bachelor's"
    
    degree_lower = degree.lower()
    
    if any(term in degree_lower for term in ['master', 'ms', 'msc', 'masters']):
        return "Master's"
    else:
        return "Bachelor's"

def extract_year(year_str):
    """Extract year from various year formats"""
    if not year_str:
        return "2020"  # Default year
    
    year_str = str(year_str)
    
    # Extract 4-digit year
    import re
    years = re.findall(r'\b(20\d{2})\b', year_str)
    
    if years:
        # Return the most recent year
        return max(years)
    
    # If format is like "2016-2020", take the end year
    if '-' in year_str:
        parts = year_str.split('-')
        if len(parts) >= 2:
            end_year = re.findall(r'\b(20\d{2})\b', parts[-1])
            if end_year:
                return end_year[0]
    
    return "2020"  # Default

def generate_job_title(skills, experience):
    """Generate appropriate job title based on skills and experience"""
    if not skills:
        return "Professional"
    
    # Handle case where skills is a string
    if isinstance(skills, str):
        if experience >= 4:
            return "Senior Professional"
        elif experience >= 2:
            return "Professional"
        else:
            return "Junior Professional"
    
    # Ensure skills is a dictionary
    if not isinstance(skills, dict):
        return "Professional"
    
    technical_skills = skills.get('technical_skills', {})
    
    # Ensure technical_skills is a dictionary
    if not isinstance(technical_skills, dict):
        technical_skills = {}
    
    # Flatten nested skills (like Microsoft Office)
    flat_skills = {}
    for skill, value in technical_skills.items():
        if isinstance(value, dict):
            flat_skills.update(value)
        else:
            flat_skills[skill] = value
    
    # Determine role based on skills
    if any(skill in flat_skills for skill in ['Python', 'Data Science', 'Machine Learning']):
        if experience >= 3:
            return "Senior Data Scientist"
        else:
            return "Data Analyst"
    
    elif any(skill in flat_skills for skill in ['JavaScript', 'React', 'Vue', 'Node']):
        if experience >= 3:
            return "Senior Software Developer"
        else:
            return "Software Developer"
    
    elif any(skill in flat_skills for skill in ['Google Ads', 'Marketing', 'SEO']):
        if experience >= 3:
            return "Marketing Manager"
        else:
            return "Digital Marketing Specialist"
    
    elif any(skill in flat_skills for skill in ['Excel', 'PowerPoint', 'Word']):
        return "Business Analyst"
    
    else:
        # Based on soft skills or general experience
        if experience >= 4:
            return "Senior Professional"
        elif experience >= 2:
            return "Professional"
        else:
            return "Junior Professional"

def convert_skills(skills_data):
    """Convert skills to the target format with 1-5 scale"""
    if not skills_data:
        return {}
    
    # Handle case where skills is a string like "Not found"
    if isinstance(skills_data, str):
        return {}
    
    # Ensure skills_data is a dictionary
    if not isinstance(skills_data, dict):
        return {}
    
    converted_skills = {}
    technical_skills = skills_data.get('technical_skills', {})
    
    # Ensure technical_skills is a dictionary
    if not isinstance(technical_skills, dict):
        technical_skills = {}
    
    # Flatten and convert technical skills
    for skill, value in technical_skills.items():
        if isinstance(value, dict):
            # Handle nested skills like Microsoft Office
            for sub_skill, sub_value in value.items():
                converted_skills[sub_skill] = str(convert_skill_value(sub_value))
        else:
            converted_skills[skill] = str(convert_skill_value(value))
    
    # Add some soft skills as technical skills if they're relevant
    soft_skills = skills_data.get('soft_skills', {})
    
    # Ensure soft_skills is a dictionary
    if not isinstance(soft_skills, dict):
        soft_skills = {}
    
    # Convert leadership and communication if high enough
    if soft_skills.get('Leadership', 0) >= 80:
        converted_skills['Leadership'] = "5"
    elif soft_skills.get('Leadership', 0) >= 60:
        converted_skills['Leadership'] = "4"
    
    if soft_skills.get('Communication', 0) >= 80:
        converted_skills['Communication'] = "5"
    elif soft_skills.get('Communication', 0) >= 60:
        converted_skills['Communication'] = "4"
    
    return converted_skills

def convert_skill_value(value):
    """Convert skill percentage to 1-5 scale"""
    if value == 0:
        return 1
    elif value <= 20:
        return 2
    elif value <= 40:
        return 2
    elif value <= 60:
        return 3
    elif value <= 80:
        return 4
    else:
        return 5

# File processing functions
def process_directory():
    """Process all JSON files from parsed directory and save to candidates directory"""
    
    # Define directories
    parsed_dir = "parsed"
    candidates_dir = "candidates"
    
    # Create candidates directory if it doesn't exist
    os.makedirs(candidates_dir, exist_ok=True)
    
    # Check if parsed directory exists
    if not os.path.exists(parsed_dir):
        print(f"Error: '{parsed_dir}' directory not found!")
        return
    
    # Get all JSON files from parsed directory
    json_files = [f for f in os.listdir(parsed_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in '{parsed_dir}' directory!")
        return
    
    print(f"Found {len(json_files)} JSON files to process...")
    
    # Process each JSON file
    for filename in json_files:
        input_path = os.path.join(parsed_dir, filename)
        output_filename = f"converted_{filename}"
        output_path = os.path.join(candidates_dir, output_filename)
        
        try:
            # Load resume data
            with open(input_path, 'r', encoding='utf-8') as f:
                resume_data = json.load(f)
            
            # Convert to standardized format
            converted_data = convert_resume_format(resume_data)
            
            # Save converted data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(converted_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Processed: {filename} -> {output_filename} ({len(converted_data)} candidates)")
            
        except Exception as e:
            print(f"✗ Error processing {filename}: {str(e)}")
    
    print(f"\nConversion complete! Check the '{candidates_dir}' directory for results.")

def process_single_file(input_file, output_file=None):
    """Process a single JSON file"""
    
    if not output_file:
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"candidates/converted_{base_name}.json"
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    try:
        # Load and convert data
        with open(input_file, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        
        converted_data = convert_resume_format(resume_data)
        
        # Save converted data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(converted_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Converted: {input_file} -> {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

# Example usage
def main():
    """Main function with command line interface"""
    import sys
    
    if len(sys.argv) > 1:
        # Process specific file
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        process_single_file(input_file, output_file)
    else:
        # Process entire directory
        process_directory()

if __name__ == "__main__":
    main()