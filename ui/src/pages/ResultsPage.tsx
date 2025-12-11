import { useNavigate, useParams } from "react-router-dom";
import { Card } from "primereact/card";
import { ProgressSpinner } from "primereact/progressspinner";
import { Message } from "primereact/message";
import { useTranscriptionPolling } from "../hooks/useTranscription";
import { TranscriptionSegmentItem } from "../components/transcription";
import { Button } from "primereact/button";
import { formatTime } from "../utils";

export function ResultsPage() {
  const navigate = useNavigate();
  const { transcriptionId } = useParams<{ transcriptionId: string }>();
  const {
    data: transcription,
    isLoading,
    error,
  } = useTranscriptionPolling(transcriptionId || "");

  if (isLoading) {
    return (
      <div
        style={{ display: "flex", justifyContent: "center", padding: "4rem" }}
      >
        <ProgressSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
        <Card>
          <Message
            severity="error"
            text="Failed to load transcription. Please try again."
          />
        </Card>
      </div>
    );
  }

  if (transcription?.status === "processing") {
    return (
      <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
        <Card>
          <div style={{ textAlign: "center" }}>
            <h2>Processing Your Transcription</h2>
            <ProgressSpinner />
            <p style={{ marginTop: "1rem", color: "#666" }}>
              Your audio is being transcribed. This may take several minutes.
            </p>
            <p style={{ fontSize: "0.9rem", color: "#999" }}>
              File: {transcription.fileName} (
              {formatTime(transcription.duration ?? 0)})
            </p>
          </div>
        </Card>
      </div>
    );
  }

  if (transcription?.status === "failed") {
    return (
      <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
        <Card>
          <Message
            severity="error"
            text={`Transcription Failed: ${transcription.metadata?.error || "Unknown error"}`}
          />
          <p style={{ marginTop: "1rem" }}>Please try again.</p>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>
        Transcription Results{" "}
        <Button onClick={() => navigate("/")}>Back</Button>
      </h1>
      <Card>
        <h3>{transcription?.fileName}</h3>
        <p>Duration: {formatTime(transcription?.duration ?? 0)}</p>
        <p>
          Status: <span style={{ color: "green" }}>Completed</span>
        </p>
        <div>
          <h4>Segments:</h4>
          {transcription?.segments && transcription.segments.length > 0 ? (
            transcription.segments.map((segment) => (
              <TranscriptionSegmentItem key={segment.id} segment={segment} />
            ))
          ) : (
            <p>No segments found in transcription.</p>
          )}
        </div>
      </Card>
    </div>
  );
}
