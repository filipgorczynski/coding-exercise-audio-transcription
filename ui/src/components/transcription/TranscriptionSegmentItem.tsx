import type { TranscriptionSegment } from "../../types/transcription";

export interface TranscriptionSegmentItemProps {
  segment: TranscriptionSegment;
}

export function TranscriptionSegmentItem({
  segment,
}: TranscriptionSegmentItemProps) {
  const { start_time: startTime, end_time: endTime, speaker, text } = segment;

  return (
    <article
      aria-label={`Transcription segment from ${startTime} to ${endTime} seconds`}
      style={{
        marginBottom: "1rem",
        padding: "0.5rem",
        border: "1px solid #ccc",
      }}
    >
      <strong>
        [{startTime} - {endTime}]
      </strong>
      {speaker && <span> - {speaker}</span>}
      <p>{text}</p>
    </article>
  );
}
