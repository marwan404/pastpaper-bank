import api from "../api.js";

function CompleteTask({ id, done }) {
  const handleClick = async () => {
    try {
      await api.put(`/tasks/${id}/toggle`);
    } catch (err) {
      console.error("Failed to toggle task", err);
    }
  };

  return (
    <button onClick={handleClick}>
      {done ? "uncheck" : "check"}
    </button>
  );
}

export default CompleteTask;
