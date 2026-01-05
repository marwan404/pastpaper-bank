import api from "../api.js";

export default function DeleteTask({ id, onDelete }) {
  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;

    try {
      await api.delete(`/tasks/${id}`);
      if (onDelete) onDelete(id); // update parent state
    } catch (err) {
      console.error("Failed to delete task", err);
    }
  };

  return (
    <button onClick={handleDelete} style={{ color: "red" }}>
      Delete
    </button>
  );
}
