import type { TranscriptionSegment } from "../../types/transcription";
import { formatTime } from "../../utils";

export interface TranscriptionSegmentItemProps {
  segment: TranscriptionSegment;
}

export function TranscriptionSegmentItem({
  segment,
}: TranscriptionSegmentItemProps) {
  const { start_time: startTime, end_time: endTime, speaker, text } = segment;

  const formattedStartTime = formatTime(startTime);
  const formattedEndTime = formatTime(endTime);

  return (
    <article
      aria-label={`Transcription segment from ${formattedStartTime} to ${formattedEndTime}`}
      style={{
        marginBottom: "1rem",
        padding: "0.5rem",
        border: "1px solid #ccc",
      }}
    >
      <strong>
        [{formattedStartTime} - {formattedEndTime}]
      </strong>
      {speaker && <span> - {speaker}</span>}
      <p>{text}</p>
    </article>
  );
}
