import { useState } from "react";
import { Card } from "primereact/card";
import { FileUpload } from "primereact/fileupload";
import { InputText } from "primereact/inputtext";
import { TabView, TabPanel } from "primereact/tabview";
import { Button } from "primereact/button";
import { ProgressBar } from "primereact/progressbar";
import { Dropdown } from "primereact/dropdown";
import { InputSwitch } from "primereact/inputswitch";
import { Fieldset } from "primereact/fieldset";
import { useFileUpload, useUrlUpload } from "../hooks/useUpload";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { DEFAULT_LANGUAGE } from "../const";

const LANGUAGE_OPTIONS = [
  { label: "English", value: "en" },
  { label: "Spanish", value: "es" },
  { label: "French", value: "fr" },
  { label: "German", value: "de" },
];

export function UploadPage() {
  const fileUploadMutation = useFileUpload();
  const urlUploadMutation = useUrlUpload();

  // Upload options (shared between both tabs)
  const [uploadOptions, setUploadOptions] = useState({
    language: DEFAULT_LANGUAGE,
    detectSpeakers: false,
  });

  // URL input state
  const [urlInput, setUrlInput] = useState("");
  const [urlError, setUrlError] = useState("");

  // File upload handler
  const handleFileUpload = (file: File) => {
    fileUploadMutation.mutate({ file, options: uploadOptions });
  };

  // URL upload handler
  const handleUrlSubmit = () => {
    // Validate URL
    if (!urlInput.trim()) {
      setUrlError("Please enter a URL");
      return;
    }

    try {
      new URL(urlInput);
      setUrlError("");
      urlUploadMutation.mutate({ url: urlInput, options: uploadOptions });
    } catch {
      setUrlError("Please enter a valid URL");
    }
  };

  // Upload options component (reusable for both tabs)
  const renderUploadOptions = () => (
    <Fieldset
      legend="Advanced Options"
      toggleable
      collapsed
      style={{ marginBottom: "1rem" }}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div>
          <label
            htmlFor="language"
            style={{ display: "block", marginBottom: "0.5rem" }}
          >
            Language
          </label>
          <Dropdown
            id="language"
            value={uploadOptions.language}
            options={LANGUAGE_OPTIONS}
            onChange={(e) =>
              setUploadOptions({ ...uploadOptions, language: e.value })
            }
            style={{ width: "100%" }}
          />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <InputSwitch
            id="detectSpeakers"
            checked={uploadOptions.detectSpeakers}
            onChange={(e) =>
              setUploadOptions({ ...uploadOptions, detectSpeakers: e.value })
            }
          />
          <label htmlFor="detectSpeakers">Detect multiple speakers</label>
        </div>
      </div>
    </Fieldset>
  );

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <h1>Transcribe Audio and Video to Text</h1>
      <Card>
        <TabView>
          <TabPanel header="Upload File">
            <div style={{ padding: "2rem" }}>
              {renderUploadOptions()}

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
                  {fileUploadMutation.progress < 100 ? (
                    <div>
                      <p
                        style={{ textAlign: "center", marginBottom: "0.5rem" }}
                      >
                        Uploading... {fileUploadMutation.progress}%
                      </p>
                      <ProgressBar value={fileUploadMutation.progress} />
                    </div>
                  ) : (
                    <div>
                      <LoadingSpinner />
                      <p style={{ textAlign: "center", marginTop: "1rem" }}>
                        Processing your audio... this may take a few minutes
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </TabPanel>

          <TabPanel header="Paste Link">
            <div style={{ padding: "2rem" }}>
              {renderUploadOptions()}

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
    </div>
  );
}
