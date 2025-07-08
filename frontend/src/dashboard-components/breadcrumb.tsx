import { Home, ChevronRight, Folder } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

export default function Breadcrumb() {
  const location = useLocation();

  // Remove the first segment (usually "dashboard")
  const paths = location.pathname.split("/").filter(Boolean).slice(1);

  const icons = [<Home className="w-4 h-4" />, <Folder className="w-4 h-4" />];

  return (
    <nav className="bg-white rounded-lg shadow flex items-center px-4 py-2 gap-2 font-inter-regular text-sm">
      {paths.map((segment, idx) => {
        const to = "/" + ["dashboard", ...paths.slice(0, idx + 1)].join("/");
        return (
          <span key={to} className="flex items-center gap-1">
            <ChevronRight className="w-4 h-4 text-secondary" />
            {idx === paths.length - 1 ? (
              <span className="flex items-center gap-1 font-semibold text-primary">
                {icons[idx] || <Folder className="w-4 h-4" />}
                {segment.charAt(0).toUpperCase() + segment.slice(1)}
              </span>
            ) : (
              <Link to={to} className="flex items-center gap-1 text-primary hover:underline">
                {icons[idx] || <Folder className="w-4 h-4" />}
                {segment.charAt(0).toUpperCase() + segment.slice(1)}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}