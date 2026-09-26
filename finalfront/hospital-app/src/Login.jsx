import { useState } from "react";
import api from "./api";

function Login({ onLogin, onRegister }) {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const login = async () => {

        if (email === "" || password === "") {
            alert("Enter email and password");
            return;
        }

        const data = new URLSearchParams();

        data.append("username", email);
        data.append("password", password);

        try {

            const response = await api.post("/login", data);

            const token = response.data.access_token;

            localStorage.setItem("token", token);

            const payload = JSON.parse(
                atob(token.split(".")[1])
            );

            alert("Login successful");

            onLogin(
                payload.sub,
                payload.role
            );

        } catch (error) {

            alert(
                error.response?.data?.detail ||
                "Invalid email or password"
            );
        }
    };

    return (
        <div className="container mt-5">

            <div
                className="card mx-auto"
                style={{ maxWidth: "450px" }}
            >

                <div className="card-header bg-dark text-white">
                    <h4>Login</h4>
                </div>

                <div className="card-body">

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

                    <button
                        className="btn btn-primary me-2"
                        onClick={login}
                    >
                        Login
                    </button>

                    <button
                        className="btn btn-secondary"
                        onClick={onRegister}
                    >
                        Register
                    </button>

                </div>

            </div>

        </div>
    );
}

export default Login;