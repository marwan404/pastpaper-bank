import { useState, useEffect } from "react";
import CompleteTask from "./complete_task.jsx";
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
  }, []);

  const handleTaskCompleted = (taskName) => {
    setTasks(prev =>
      prev.filter(task => task.name !== taskName)
    );
  };

  return (
    <ul>
      {tasks.map(task => (
        <li key={task.name}>
          {task.name}
          <CompleteTask
            name={task.name}
            onTaskCompleted={handleTaskCompleted}
          />
        </li>
      ))}
    </ul>
  );
}

export default DisplayTasks;
