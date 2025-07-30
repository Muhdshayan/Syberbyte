import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Document, Page, pdfjs } from 'react-pdf';

// Set worker source to match your pdfjs-dist version
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;


export default function Demo() {
  const [numPages, setNumPages] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pdfUrl = "/resume.pdf";

  const goToPrevPage = () => {
    setCurrentPage(page => Math.max(1, page - 1));
  };

  const goToNextPage = () => {
    setCurrentPage(page => Math.min(numPages, page + 1));
  };

  return (
    <div className="w-full min-h-screen flex flex-col bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto w-full">
        <h1 className="text-3xl font-bold mb-6">Candidate Profile</h1>
        
        <Card className="w-full p-5 flex flex-col gap-2 shadow-sm hover:shadow-lg hover:scale-[1.02] transition-all duration-300 cursor-pointer">
          <div className="flex justify-between gap-2 items-center font-inter-regular">
            <div className="flex items-center gap-2">
              <span className="text-lg text-left font-poppins-semibold">Candidate 1</span>
              <Badge className="green !text-white !text-sm transition-colors self-center h-fit">
                not_selected
              </Badge>
            </div>
            <span className="bg-green text-white rounded-full px-4 py-1 text-sm font-medium transition-colors hover:bg-green-600">
              99
            </span>
          </div>
          
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mt-2 gap-2">
            <p className="font-inter-regular text-secondary text-left text-sm">
              <span className="font-inter-medium text-primary text-md mr-2">AI Recommendation:</span>
              AI recommended
            </p>
            
            <Dialog>
              <DialogTrigger asChild>
                <Button
                  className="!bg-blue !text-sm hover:!bg-blue-700 hover:scale-105 transition-all duration-200"
                >
                  View Resume
                </Button>
              </DialogTrigger>
              
              <DialogContent className="max-h-[90vh] w-full">
                <div className="h-[80vh] overflow-y-scroll flex flex-col">
                  <Document
                    file={pdfUrl}
                    onLoadSuccess={({ numPages }) => {
                      setNumPages(numPages);
                      setCurrentPage(1); // Reset to first page when PDF loads
                    }}
                    loading={<div>Loading PDF...</div>}
                    className="flex-1 flex justify-center"
                  >
                    <Page 
                      pageNumber={currentPage} 
                      scale={window.innerWidth > 600 ? 0.8 : 0.5}
                      renderAnnotationLayer={false} 
                      renderTextLayer={false}
                      className="mx-auto"
                    />
                  </Document>
                  
                  {/* Page Navigation Controls */}
                  {numPages > 1 && (
                    <div className="flex justify-center items-center gap-4 py-4 bg-white border-t">
                      <Button
                        onClick={goToPrevPage}
                        disabled={currentPage <= 1}
                        variant="outline"
                        size="sm"
                      >
                        Previous
                      </Button>
                      
                      <span className="text-sm font-medium">
                        Page {currentPage} of {numPages}
                      </span>
                      
                      <Button
                        onClick={goToNextPage}
                        disabled={currentPage >= numPages}
                        variant="outline"
                        size="sm"
                      >
                        Next
                      </Button>
                    </div>
                  )}
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </Card>
      </div>
    </div>
  );
}