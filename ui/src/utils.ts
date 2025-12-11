/**
 * Format seconds to MM:SS format
 * @param seconds - Time in seconds
 * @returns Formatted time string (mm:ss:SS)
 */
export function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const secs = (seconds % 60).toFixed(2);
  return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(5, "0")}`;
}
