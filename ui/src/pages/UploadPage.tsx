import { useState, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Card } from "primereact/card";
import { FileUpload } from "primereact/fileupload";
import { InputText } from "primereact/inputtext";
import { TabView, TabPanel } from "primereact/tabview";
import { Button } from "primereact/button";
import { ProgressBar } from "primereact/progressbar";
import { useFileUpload, useUrlUpload } from "../hooks/useUpload";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { TranscriptionList } from "../components/transcription";

export function UploadPage() {
  const queryClient = useQueryClient();
  const fileUploadMutation = useFileUpload();
  const urlUploadMutation = useUrlUpload();
  const [urlInput, setUrlInput] = useState("");
  const [urlError, setUrlError] = useState("");

  useEffect(() => {
    if (fileUploadMutation.isSuccess || urlUploadMutation.isSuccess) {
      queryClient.invalidateQueries({ queryKey: ["transcriptions"] });
    }
  }, [fileUploadMutation.isSuccess, urlUploadMutation.isSuccess, queryClient]);

  const handleFileUpload = (file: File) => {
    fileUploadMutation.mutate({ file });
  };

  const handleUrlSubmit = () => {
    if (!urlInput.trim()) {
      setUrlError("Please enter a URL");
      return;
    }

    try {
      new URL(urlInput);
      setUrlError("");
      urlUploadMutation.mutate({ url: urlInput });
    } catch {
      setUrlError("Please enter a valid URL");
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <h1>TransCribe: A/VtoText</h1>
      <Card>
        <TabView>
          <TabPanel header="Upload File">
            <div style={{ padding: "2rem" }}>
              {fileUploadMutation.error && (
                <div style={{ marginBottom: "1rem" }}>
                  <ErrorMessage
                    message={
                      fileUploadMutation.error.message || "Upload failed"
                    }
                  />
                </div>
              )}

              <div style={{ textAlign: "center", marginBottom: "1rem" }}>
                <FileUpload
                  mode="basic"
                  customUpload={true}
                  uploadHandler={(e) => handleFileUpload(e.files[0])}
                  chooseLabel="Select audio or video file"
                  disabled={fileUploadMutation.isPending}
                  accept="audio/*,video/*"
                />
              </div>

              {fileUploadMutation.isPending && (
                <div style={{ marginTop: "1rem" }}>
                  {/* {fileUploadMutation.progress < 100 ? (
                    <div>
                      <p
                        style={{ textAlign: "center", marginBottom: "0.5rem" }}
                      >
                        Uploading... {fileUploadMutation.progress}%
                      </p>
                      <ProgressBar value={fileUploadMutation.progress} />
                    </div>
                  ) : ( */}
                  <div>
                    <LoadingSpinner />
                    <p style={{ textAlign: "center", marginTop: "1rem" }}>
                      Processing your file... this may take a few minutes
                    </p>
                  </div>
                  {/* )} */}
                </div>
              )}
            </div>
          </TabPanel>

          <TabPanel header="Paste Link">
            <div style={{ padding: "2rem" }}>
              {urlUploadMutation.error && (
                <div style={{ marginBottom: "1rem" }}>
                  <ErrorMessage
                    message={urlUploadMutation.error.message || "Upload failed"}
                  />
                </div>
              )}

              {urlError && (
                <div style={{ marginBottom: "1rem" }}>
                  <ErrorMessage message={urlError} />
                </div>
              )}

              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "1rem",
                }}
              >
                <InputText
                  value={urlInput}
                  onChange={(e) => {
                    setUrlInput(e.target.value);
                    setUrlError("");
                  }}
                  placeholder="Enter URL of audio or video file"
                  disabled={urlUploadMutation.isPending}
                  style={{ width: "100%" }}
                />
                <Button
                  label={
                    urlUploadMutation.isPending
                      ? "Uploading..."
                      : "Upload from URL"
                  }
                  onClick={handleUrlSubmit}
                  disabled={urlUploadMutation.isPending}
                  loading={urlUploadMutation.isPending}
                  style={{ width: "100%" }}
                />
              </div>

              {urlUploadMutation.isPending && (
                <div style={{ marginTop: "1rem" }}>
                  <LoadingSpinner />
                  <p style={{ textAlign: "center", marginTop: "1rem" }}>
                    Downloading and processing your audio... this may take a few
                    minutes
                  </p>
                </div>
              )}
            </div>
          </TabPanel>
        </TabView>
      </Card>

      <div style={{ marginTop: "2rem" }}>
        <TranscriptionList />
      </div>
    </div>
  );
}
