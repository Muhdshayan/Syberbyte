interface NoDataProps {
  imageSrc?: string;
  title: string;
  subtitle?: string;
  className?: string;
}

export default function NoData({ 
  imageSrc = "/nothingtoshow.png", 
  title, 
  subtitle,
  className = ""
}: NoDataProps) {
  return (
    <div className={`flex flex-col items-center justify-center h-screen ${className}`}>
      <img
        src={imageSrc}
        alt={title}
        className="mb-4"
      />
      <h2 className="text-xl font-poppins-semibold mb-2">{title}</h2>
      {subtitle && (
        <p className="text-gray-600 font-inter-regular">{subtitle}</p>
      )}
    </div>
  );
}