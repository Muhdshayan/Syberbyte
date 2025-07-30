"use client"

import type React from "react"
import { useState, useCallback, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { X, Upload, FileText, CheckCircle, AlertCircle, Folder, Loader2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { useRecruiterStore, type Job, type UploadFile } from "@/dashboard/RecruiterDashboard/recruiter-store"
import { toast } from "sonner"

interface BulkUploadProps {
  onClose: () => void
  jobId: Job["job_id"]
}

export function BulkUpload({ onClose, jobId }: BulkUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false)

  // Get store state and actions
  const {
    uploadFiles,
    uploadProgress,
    isUploading,
    uploadError,
    addUploadFiles,
    removeUploadFile,
    clearUploadFiles,
    updateFileProgress,
    updateFileStatus,
    processBulkUpload,
    error
  } = useRecruiterStore()

  // Clear upload files when component mounts
  useEffect(() => {
    clearUploadFiles()
  }, [clearUploadFiles])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)

    const items = Array.from(e.dataTransfer.items)
    processItems(items)
  }, [])

  const getFileType = (fileName: string): "pdf" | "docx" | "doc" => {
  const lowerName = fileName.toLowerCase();
  if (lowerName.endsWith(".pdf")) return "pdf";
  if (lowerName.endsWith(".docx")) return "docx";
  if (lowerName.endsWith(".doc")) return "doc";
  
  // Show toast for unsupported file type
  toast.error(`This format is not accepted: ${fileName}. Please upload PDF or Word documents only.`);
  throw new Error("Unsupported file type");
};

const isValidFileType = (file: File): boolean => {
  const validTypes = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ];
  const validExtensions = [".pdf", ".doc", ".docx"];
  
  return validTypes.includes(file.type) || 
         validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
};

const processItems = async (items: DataTransferItem[]) => {
  const newFiles: UploadFile[] = []
  let hasInvalidFiles = false

  for (const item of items) {
    if (item.kind === "file") {
      const file = item.getAsFile()
      if (file) {
        if (!isValidFileType(file)) {
          // Show toast for each invalid file
          toast.error(`This format is not accepted: ${file.name}. Please upload PDF or Word documents only.`);
          hasInvalidFiles = true
          continue
        }

        try {
          newFiles.push({
            id: Math.random().toString(36),
            name: file.name,
            size: file.size,
            status: "pending",
            progress: 0,
            type: getFileType(file.name),
            file: file,
          })
        } catch (error) {
          // Error already handled in getFileType with toast
          hasInvalidFiles = true
        }
      }
    }
  }

  if (newFiles.length > 0) {
    addUploadFiles(newFiles)
    toast.success(`${newFiles.length} valid files added`)
  } else if (hasInvalidFiles) {
    toast.error("No valid files found. Please select PDF or Word documents only.")
  }
}

const processFileList = (files: FileList) => {
  const newFiles: UploadFile[] = []
  let hasInvalidFiles = false

  Array.from(files).forEach((file) => {
    if (!isValidFileType(file)) {
      // Show toast for each invalid file
      toast.error(`This format is not accepted: ${file.name}. Please upload PDF or Word documents only.`);
      hasInvalidFiles = true
      return
    }

    try {
      newFiles.push({
        id: Math.random().toString(36),
        name: file.webkitRelativePath || file.name,
        size: file.size,
        status: "pending" as const,
        progress: 0,
        type: getFileType(file.name),
        file: file,
      })
    } catch (error) {
      // Error already handled in getFileType with toast
      hasInvalidFiles = true
    }
  })

  if (newFiles.length > 0) {
    addUploadFiles(newFiles)
    toast.success(`${newFiles.length} valid files added`)
  } else if (hasInvalidFiles) {
    toast.error("No valid files found. Please select PDF or Word documents only.")
  }
}


  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files
    if (selectedFiles) {
      processFileList(selectedFiles)
    }
    e.target.value = ""
  }

  const handleFolderInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files
    if (selectedFiles) {
      processFileList(selectedFiles)
    }
    e.target.value = ""
  }

  const handleProcessFiles = async () => {
    if (uploadFiles.length === 0) {
      toast.error("Please select files to upload")
      return
    }

    try {
      // First, simulate individual file processing for UI feedback
      for (let i = 0; i < uploadFiles.length; i++) {
        const file = uploadFiles[i]
        updateFileStatus(file.id, "processing")

        // Simulate progress for each file
        for (let progress = 0; progress <= 100; progress += 20) {
          await new Promise((resolve) => setTimeout(resolve, 100))
          updateFileProgress(file.id, progress)
        }
      }

      // Now process the actual upload
      const result = await processBulkUpload(jobId)

      // Mark files as completed or error based on result
      uploadFiles.forEach((file) => {
        const hasError = result.errors.some(error => error.fileName === file.name)
        updateFileStatus(
          file.id,
          hasError ? "error" : "completed",
          hasError ? result.errors.find(e => e.fileName === file.name)?.error : undefined
        )
        updateFileProgress(file.id, 100)
      })

      toast.success(`Upload completed! ${result.successCount} files processed successfully`)

    } catch (error) {
      console.error("Upload failed:", error)
      toast.error("Upload failed. Please try again.")
    }
  }

  const getStatusIcon = (status: UploadFile["status"]) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-500" />
      case "processing":
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
      default:
        return <FileText className="w-4 h-4 text-gray-400" />
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const completedCount = uploadFiles.filter((f) => f.status === "completed").length
  const errorCount = uploadFiles.filter((f) => f.status === "error").length
  const isProcessingComplete = completedCount + errorCount === uploadFiles.length && uploadFiles.length > 0

  const handleClose = () => {
    if (isUploading) {
      toast.error("Cannot close while upload is in progress")
      return
    }
    clearUploadFiles()
    onClose()
  }

  // Handle backdrop click to close dialog
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleClose()
    }
  }

  return (
    <div
      className="fixed inset-0 font-inter-regular bg-black flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg w-full max-w-6xl h-[85vh] flex flex-col shadow-2xl">
        <div className="flex-shrink-0 p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-poppins-semibold text-primary text-left">Bulk Resume Upload</h2>
              <p className="text-secondary text-left mt-1">
                Upload individual files, entire folders, or Excel sheets with candidate data
              </p>
            </div>
            <Button
              className="!bg-blue"
              size="sm"
              onClick={handleClose}
              disabled={isUploading}
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-6">
            {/* Upload Area */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${isDragOver ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"
                } ${isUploading ? "pointer-events-none opacity-50" : ""}`}
            >
              <div className="space-y-4">
                <div className="flex justify-center">
                  <div className="p-3 bg-blue-100 rounded-full">
                    <Folder className="w-8 h-8 text-blue-600" />
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-900">Drop entire folders or select multiple files</h3>
                  <p className="text-gray-500 mt-1">
                    Supports PDF, DOC, DOCX resume files. Drop entire folders or select
                    multiple files.
                  </p>
                </div>

                <div className="flex justify-center space-x-4">
                  <Button
                    className="!bg-blue-600 !text-sm"
                    onClick={() => document.getElementById("file-input")?.click()}
                    disabled={isUploading}
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Select Files
                  </Button>
                  <Button
                    className="!bg-blue-600 !text-sm"
                    onClick={() => document.getElementById("folder-input")?.click()}
                    disabled={isUploading}
                  >
                    <Folder className="w-4 h-4 mr-2" />
                    Select Folder
                  </Button>
                </div>
                {error && (
                  <p className="text-red-500 text-sm mt-2">
                    {error}
                  </p>)}

                <input
                  id="file-input"
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx,.xlsx,.xls,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                  onChange={handleFileInput}
                  className="hidden"
                />
                <input
                  id="folder-input"
                  type="file"
                  multiple
                  // @ts-ignore
                  webkitdirectory=""
                  directory=""
                  onChange={handleFolderInput}
                  className="hidden"
                />
              </div>
            </div>

            {/* Error Display */}
            {uploadError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
                  <div>
                    <h3 className="text-sm font-medium text-red-800">Upload Error</h3>
                    <p className="text-sm text-red-700 mt-1">{uploadError}</p>
                  </div>
                </div>
              </div>
            )}

            {/* File List */}
            {uploadFiles.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium">Files ({uploadFiles.length})</h3>
                  <div className="flex space-x-2">
                    {completedCount > 0 && (
                      <Badge className="bg-green-100 text-green">{completedCount} completed</Badge>
                    )}
                    {errorCount > 0 && <Badge className="bg-red-100 text-red-800">{errorCount} failed</Badge>}
                  </div>
                </div>

                {isUploading && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Overall Progress</span>
                      <span>{Math.round(uploadProgress)}%</span>
                    </div>
                    <Progress value={uploadProgress} className="w-full shadow-2xl [&>div]:bg-blue" />
                  </div>
                )}

                <div className="border rounded-lg">
                  <div className="space-y-1 p-2">
                    {uploadFiles.map((file) => (
                      <div
                        key={file.id}
                        className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors"
                      >
                        {getStatusIcon(file.status)}

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                            <Badge variant="outline" className="text-xs">
                              {["pdf", "doc", "docx"].includes(file.type)
                                ? file.type.toUpperCase()
                                : "Unknown"}
                            </Badge>
                          </div>
                          <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                          {file.errorMessage && (
                            <div className="text-xs text-red-600 mt-1">
                              {Object.entries(file.errorMessage).map(([key, messages], i) => (
                                <p key={i}>{key}: {Array.isArray(messages) ? messages.join(', ') : messages}</p>
                              ))}
                            </div>
                          )}

                        </div>

                        {file.status === "processing" && (
                          <div className="w-20">
                            <Progress value={file.progress} className="h-2 [&>div]:bg-blue" />
                          </div>
                        )}

                        {file.status === "pending" && !isUploading && (
                          <Button
                            size="sm"
                            onClick={() => removeUploadFile(file.id)}
                            className="hover:bg-red-50 !bg-red-500"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Fixed Footer */}
        <div className="flex-shrink-0 p-6 border-t border-gray-200 bg-gray-50 rounded-b-lg">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              {uploadFiles.length > 0 && (
                <span>
                  {uploadFiles.length} files selected • {completedCount} completed • {errorCount} failed
                </span>
              )}
            </div>
            <div className="flex space-x-3">
              {isProcessingComplete ? (
                <Button
                  onClick={handleClose}
                  className="!bg-gradient-to-bl from-green to-blue !text-sm"
                >
                  Done
                </Button>
              ) : (
                <Button
                  onClick={handleProcessFiles}
                  className="!bg-blue !text-sm"
                  disabled={isUploading || uploadFiles.length === 0}
                >
                  {isUploading ? "Processing..." : `Process ${uploadFiles.length} Files`}
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}