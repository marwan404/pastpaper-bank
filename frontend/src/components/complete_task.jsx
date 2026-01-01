import api from "../api.js";

function CompleteTask({ name, onTaskCompleted }) {
  const handleClick = async () => {
    try {
      await api.put(`/tasks/${name}`, { name, done: true });
      onTaskCompleted(name);
    } catch (err) {
      console.error("Failed to complete task", err);
    }
  };

  return (
    <button onClick={handleClick}>
      complete
    </button>
  );
}

export default CompleteTask;
