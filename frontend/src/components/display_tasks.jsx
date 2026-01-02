import { useState, useEffect, useCallback, useRef } from "react";
import CompleteTask from "./complete_task.jsx";
import api from "../api.js";

export default function DisplayTasks() {
  const [tasks, setTasks] = useState([]);
  const wsRef = useRef(null);

  // fetch tasks from backend
  const fetchTasks = useCallback(async () => {
    try {
      const res = await api.get("/tasks");
      /** @type {{ tasks: Array<{ id: number, name: string, done: boolean }> }} */
      const data = res.data;

      setTasks(data.tasks);

    } catch (err) {
      console.error("Failed to fetch tasks", err);
    }
  }, []);

  // initial fetch + websocket setup
  useEffect(() => {
    void fetchTasks();

    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onopen = () => console.log("WS connected");
    ws.onmessage = () => fetchTasks(); // refresh on server broadcast
    ws.onclose = () => console.log("WS disconnected");
    wsRef.current = ws;

    return () => ws.close();
  }, [fetchTasks]);

  // update a single task locally (optimistic UI)
  const updateTaskLocally = (id, done) => {
    setTasks(prev =>
      prev.map(task => (task.id === id ? { ...task, done } : task))
    );
  };

  return (
    <ul>
      {tasks.map(task => (
        <li key={task.id} style={{ marginBottom: "8px" }}>
          {task.name} -{" "}
          <CompleteTask
            id={task.id}
            done={task.done}
            onToggle={updateTaskLocally}
          />
        </li>
      ))}
    </ul>
  );
}
