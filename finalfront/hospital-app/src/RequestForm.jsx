import { useState } from "react";
import api from "./api";

function RequestForm({ onAdd, request, onUpdate, onBack }) {

    const [title, setTitle] = useState(
        request ? request.title : ""
    );

    const [description, setDescription] = useState(
        request ? request.description : ""
    );

    const [department, setDepartment] = useState(
        request ? request.department : "Emergency"
    );

    const [category, setCategory] = useState(
        request ? request.category : "Hardware"
    );

    const [priority, setPriority] = useState(
        request ? request.priority : "Medium"
    );

    const saveRequest = async () => {

        if (title === "" || description === "") {
            alert("Fill all fields");
            return;
        }

        const requestData = {
            title: title,
            description: description,
            department: department,
            category: category,
            priority: priority,
            status: request ? request.status : "New"
        };

        const token = localStorage.getItem("token");

        try {

            if (request) {

                const response = await api.put(
                    `/requests/${request.id}`,
                    requestData,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    }
                );

                onUpdate(
                    request.id,
                    response.data
                );

            } else {

                const response = await api.post(
                    "/requests",
                    requestData,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    }
                );

                onAdd(response.data);
            }

        } catch (error) {

            alert(
                error.response?.data?.detail ||
                "Something went wrong"
            );
        }
    };

    return (
        <div className="container mt-4">

            <div className="card">

                <div className="card-header bg-dark text-white">

                    <h4>
                        {request
                            ? "Edit Hospital Request"
                            : "New Hospital Request"}
                    </h4>

                </div>

                <div className="card-body">

                    <label className="form-label">
                        Title
                    </label>

                    <input
                        type="text"
                        className="form-control mb-3"
                        value={title}
                        onChange={(e) =>
                            setTitle(e.target.value)
                        }
                        placeholder="Enter request title"
                    />

                    <label className="form-label">
                        Description
                    </label>

                    <textarea
                        className="form-control mb-3"
                        value={description}
                        onChange={(e) =>
                            setDescription(e.target.value)
                        }
                        placeholder="Enter description"
                    />

                    <label className="form-label">
                        Department
                    </label>

                    <select
                        className="form-select mb-3"
                        value={department}
                        onChange={(e) =>
                            setDepartment(e.target.value)
                        }
                    >
                        <option>Emergency</option>
                        <option>Radiology</option>
                        <option>Laboratory</option>
                        <option>Pharmacy</option>
                        <option>Administration</option>
                        <option>IT Support</option>
                    </select>

                    <label className="form-label">
                        Category
                    </label>

                    <select
                        className="form-select mb-3"
                        value={category}
                        onChange={(e) =>
                            setCategory(e.target.value)
                        }
                    >
                        <option>Hardware</option>
                        <option>Software</option>
                        <option>Network</option>
                        <option>Other</option>
                    </select>

                    <label className="form-label">
                        Priority
                    </label>

                    <select
                        className="form-select mb-3"
                        value={priority}
                        onChange={(e) =>
                            setPriority(e.target.value)
                        }
                    >
                        <option>Low</option>
                        <option>Medium</option>
                        <option>High</option>
                    </select>

                    <button
                        className="btn btn-primary me-2"
                        onClick={saveRequest}
                    >
                        {request
                            ? "Update Request"
                            : "Create Request"}
                    </button>

                    <button
                        className="btn btn-secondary"
                        onClick={onBack}
                    >
                        Back
                    </button>

                </div>

            </div>

        </div>
    );
}

export default RequestForm;