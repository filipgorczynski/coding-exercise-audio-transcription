import { useNavigate, useParams } from "react-router-dom";
import { Card } from "primereact/card";
import { ProgressSpinner } from "primereact/progressspinner";
import { Message } from "primereact/message";
import { useTranscriptionPolling } from "../hooks/useTranscription";
import { TranscriptionSegmentItem } from "../components/transcription";
import { Button } from "primereact/button";
import { formatTime } from "../utils";

const SPEAKER_COLORS = [
  "#FFE6E6",  // Light Red
  "#E6F7FF",  // Light Blue
  "#FFF7E6",  // Light Orange
  "#F0FFE6",  // Light Green
  "#FFE6F7",  // Light Pink
  "#E6FFFA",  // Light Teal
  "#FFF0E6",  // Light Peach
  "#F0E6FF",  // Light Purple
  "#FFFAE6",  // Light Yellow
];
const DEFAULT_COLOR = "#F5F5F5";  // Light gray for unknown/undefined speakers

const getSpeakerColor = (speaker: string | undefined): string => {
  if (!speaker || speaker.trim() === "" || speaker === "UNKNOWN") {
    return DEFAULT_COLOR;
  }

  // Extract number from speaker ID (e.g., "SPEAKER_00" -> 0, "SPEAKER_01" -> 1)
  const match = speaker.match(/\d+$/);
  const index = match ? parseInt(match[0], 10) % SPEAKER_COLORS.length : 0;

  return SPEAKER_COLORS[index];
};

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
          <Message severity="error" text="Transcription Failed" />
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
              <TranscriptionSegmentItem
                key={segment.id}
                segment={segment}
                backgroundColor={getSpeakerColor(segment.speaker)}
              />
            ))
          ) : (
            <p>No segments found in transcription.</p>
          )}
        </div>
      </Card>
    </div>
  );
}
