import {useState} from "react";
import api from "../api.js";

function AddTask({onTaskAdded}){
    const[name, setName] = useState("");

    const handleSubmit = async (e) =>{
        e.preventDefault();
        if(!name) return;

        try {
            const response = await api.post("/tasks", {name,done:false});
            setName("");
            if(onTaskAdded) onTaskAdded(response.data);
        } catch (err){
            console.error("failed to add task", err);
        }
    };

    return(
      <>
          <form onSubmit={handleSubmit}>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="New task"
              />
              <button type={"submit"}>Add Task</button>
          </form>
      </>
    );
}

export default AddTask;