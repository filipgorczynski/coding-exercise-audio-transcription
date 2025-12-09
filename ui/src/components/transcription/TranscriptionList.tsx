import { useNavigate } from "react-router-dom";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { Tag } from "primereact/tag";
import { Card } from "primereact/card";
import { useListTranscriptions } from "../../hooks/useTranscription";
import type { TranscriptionItem } from "../../types/transcription";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { ErrorMessage } from "../common/ErrorMessage";
import { formatTime } from "../../utils";

export function TranscriptionList() {
  const navigate = useNavigate();
  const {
    data: transcriptions = [],
    isLoading,
    error,
  } = useListTranscriptions();

  const handleRowClick = (e: any) => {
    navigate(`/results/${e.data.id}`);
  };

  const statusBodyTemplate = (rowData: TranscriptionItem) => {
    const statusConfig = {
      pending: { severity: "secondary" as const, icon: "pi-clock" },
      processing: { severity: "info" as const, icon: "pi-spin pi-spinner" },
      completed: { severity: "success" as const, icon: "pi-check" },
      failed: { severity: "danger" as const, icon: "pi-times" },
    };

    const config = statusConfig[rowData.status];
    return (
      <Tag
        severity={config.severity}
        icon={`pi ${config.icon}`}
        value={rowData.status.charAt(0).toUpperCase() + rowData.status.slice(1)}
      />
    );
  };

  const durationBodyTemplate = (rowData: TranscriptionItem) => {
    return rowData.duration ? formatTime(rowData.duration) : "N/A";
  };

  if (isLoading) return <LoadingSpinner />;

  if (error) {
    return (
      <Card>
        <ErrorMessage message="Failed to load transcriptions. Please try again." />
      </Card>
    );
  }

  if (transcriptions.length === 0) {
    return (
      <Card>
        <div style={{ textAlign: "center", padding: "3rem", color: "#666" }}>
          <i
            className="pi pi-inbox"
            style={{ fontSize: "3rem", display: "block", marginBottom: "1rem" }}
          />
          <p>No transcriptions yet. Upload a file to get started!</p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <h2 style={{ marginTop: 0 }}>Your Transcriptions</h2>
      <DataTable
        value={transcriptions}
        onRowClick={handleRowClick}
        selectionMode="single"
        stripedRows
        style={{ cursor: "pointer" }}
      >
        <Column field="file_name" header="File Name" />
        <Column
          field="status"
          header="Status"
          body={statusBodyTemplate}
          style={{ width: "150px" }}
        />
        <Column
          field="duration"
          header="Duration"
          body={durationBodyTemplate}
          style={{ width: "120px" }}
        />
      </DataTable>
    </Card>
  );
}
