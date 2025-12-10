import { ProgressSpinner } from "primereact/progressspinner";

export function LoadingSpinner() {
  return (
    <div style={{ display: "flex", justifyContent: "center", padding: "2rem" }}>
      <ProgressSpinner />
    </div>
  );
}
