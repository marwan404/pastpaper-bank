import api from "../api.js";
import { useState } from "react";

export default function CompleteTask({ id, done: initialDone, onToggle }) {
  const [done, setDone] = useState(initialDone);

  const handleClick = async () => {
    try {
      const res = await api.put(`/tasks/${id}/toggle`);
      const newState = res.data.done;

      setDone(newState);            // update button text immediately
      if (onToggle) onToggle(id, newState); // update parent state
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
