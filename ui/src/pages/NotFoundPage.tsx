import { Card } from "primereact/card";
import { Button } from "primereact/button";
import { useNavigate } from "react-router-dom";
import styles from "./NotFoundPage.module.css";

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className={styles.container}>
      <Card>
        <h1>404 - Page Not Found</h1>
        <p>The page you are looking for does not exist.</p>
        <Button
          label="Go Home"
          icon="pi pi-home"
          onClick={() => navigate("/")}
        />
      </Card>
    </div>
  );
}
