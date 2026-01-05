import api from "../api.js";
import { useState } from "react";

export default function RenameTask({ id, initialName, onNameChanged }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState(String(initialName));
  const [loading, setLoading] = useState(false);

  const handleRename = async () => {
    if (!name.trim()) return;

    try {
      setLoading(true);

      await api.put(`/tasks/${id}/change`, null, {
        params: { task_name: name },
      });

      if (onNameChanged) onNameChanged(id, name);
      setOpen(false);
    } catch (err) {
      console.error("Failed to rename task", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button onClick={() => setOpen(true)}>
        Rename
      </button>

      {open && (
        <div className={"overlayStyle"}>
          <div className={"modalStyle"}>
            <h3>Rename Task</h3>

            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />

            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button onClick={handleRename} disabled={loading}>
                {loading ? "Saving..." : "Save"}
              </button>

              <button onClick={() => {
                setName(initialName);
                setOpen(false);
              }}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
