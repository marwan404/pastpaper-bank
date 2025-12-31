import { useState, useEffect } from "react";
import api from "../api.js";

function DisplayTasks() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get("/tasks");
        setTasks(response.data.tasks);
      } catch (err) {
        console.error("Failed to load tasks", err);
      }
    };

    fetchData();
  }, []); // run once on mount

  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.name}>{task.name}</li>
      ))}
    </ul>
  );
}

export default DisplayTasks;
