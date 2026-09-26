import { useState } from "react";
import api from "./api";

function Register({ onRegister }) {

    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [role, setRole] = useState("Department Staff");
    const [department, setDepartment] = useState("Emergency");

    const register = async () => {

        if (
            name === "" ||
            email === "" ||
            password === ""
        ) {
            alert("Fill all fields");
            return;
        }

        const userData = {
            name: name,
            email: email,
            password: password,
            role: role,
            department: department,
            status: "active"
        };

        try {

            await api.post(
                "/users",
                userData
            );

            alert("User created successfully");

            setName("");
            setEmail("");
            setPassword("");

            onRegister();

        } catch (error) {

            alert(
                error.response?.data?.detail ||
                "Could not create user"
            );
        }
    };

    return (
        <div className="container mt-5">

            <div
                className="card mx-auto"
                style={{ maxWidth: "500px" }}
            >

                <div className="card-header bg-dark text-white">

                    <h4>Create User</h4>

                </div>

                <div className="card-body">

                    <label className="form-label">
                        Name
                    </label>

                    <input
                        type="text"
                        className="form-control mb-3"
                        value={name}
                        onChange={(e) =>
                            setName(e.target.value)
                        }
                        placeholder="Enter name"
                    />

                    <label className="form-label">
                        Email
                    </label>

                    <input
                        type="email"
                        className="form-control mb-3"
                        value={email}
                        onChange={(e) =>
                            setEmail(e.target.value)
                        }
                        placeholder="Enter email"
                    />

                    <label className="form-label">
                        Password
                    </label>

                    <input
                        type="password"
                        className="form-control mb-3"
                        value={password}
                        onChange={(e) =>
                            setPassword(e.target.value)
                        }
                        placeholder="Enter password"
                    />

                    <label className="form-label">
                        Role
                    </label>

                    <select
                        className="form-select mb-3"
                        value={role}
                        onChange={(e) =>
                            setRole(e.target.value)
                        }
                    >
                        <option>Department Staff</option>
                        <option>Support Engineer</option>
                        <option>Team Lead</option>
                        <option>Admin</option>
                    </select>

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

                    <button
                        className="btn btn-primary me-2"
                        onClick={register}
                    >
                        Create User
                    </button>

                    <button
                        className="btn btn-secondary"
                        onClick={onRegister}
                    >
                        Back to Login
                    </button>

                </div>

            </div>

        </div>
    );
}

export default Register;