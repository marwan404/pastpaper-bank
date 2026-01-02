import { useState, useEffect, useCallback } from "react";
import CompleteTask from "./complete_task.jsx";
import api from "../api.js";

function DisplayTasks() {
  const [tasks, setTasks] = useState([]);

  const fetchTasks = useCallback(async () => {
    try {
      const res = await api.get("/tasks");
      setTasks(res.data.tasks);
    } catch (err) {
      console.error("Failed to fetch tasks", err);
    }
  }, []);

  useEffect(() => {
    fetchTasks(); // initial load

    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onmessage = () => {
      fetchTasks(); // re-fetch on updates
    };

    return () => ws.close();
  }, [fetchTasks]);

  return (
    <ul>
      {tasks.map(task => (
        <li key={task.id}>
          {task.name}
          <CompleteTask
            id={task.id}
            done={task.done}
          />
        </li>
      ))}
    </ul>
  );
}

export default DisplayTasks;
