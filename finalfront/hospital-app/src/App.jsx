import { useState } from "react";
import Login from "./Login";
import Register from "./Register";
import RequestList from "./RequestList";
import RequestForm from "./RequestForm";
import api from "./api";
import "./App.css";

function App() {

    const [page, setPage] = useState("login");
    const [user, setUser] = useState(null);

    const [selectedRequest, setSelectedRequest] = useState(null);

    const [requests, setRequests] = useState([]);

    const login = async (email, role) => {

        setUser({
            email: email,
            role: role
        });

        const token = localStorage.getItem("token");

        try {

            const response = await api.get("/requests", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            setRequests(response.data);

            setPage("requests");

        } catch (error) {

            alert(
                error.response?.data?.detail ||
                "Could not load requests"
            );
        }
    };

    const logout = () => {

        localStorage.removeItem("token");

        setUser(null);
        setRequests([]);

        setPage("login");
    };

    const addRequest = (request) => {

        setRequests([
            ...requests,
            request
        ]);

        setPage("requests");
    };

    const deleteRequest = async (id) => {

        const token = localStorage.getItem("token");

        try {

            await api.delete(
                `/requests/${id}`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            setRequests(
                requests.filter(
                    (request) => request.id !== id
                )
            );

        } catch (error) {

            alert(
                error.response?.data?.detail ||
                "Could not delete request"
            );
        }
    };

    const editRequest = (request) => {

        setSelectedRequest(request);

        setPage("edit");
    };

    const updateRequest = (id, updatedRequest) => {

        setRequests(
            requests.map((request) =>
                request.id === id
                    ? updatedRequest
                    : request
            )
        );

        setSelectedRequest(null);

        setPage("requests");
    };

    return (
        <div>

            <nav className="navbar navbar-dark bg-dark px-4">

                <span className="navbar-brand mb-0 h1">
                    Hospital Service Desk
                </span>

                {user && (
                    <div>

                        <button
                            className="btn btn-light me-2"
                            onClick={() => setPage("requests")}
                        >
                            Requests
                        </button>

                        <button
                            className="btn btn-light me-2"
                            onClick={() => setPage("new")}
                        >
                            New Request
                        </button>

                        <button
                            className="btn btn-light me-2"
                            onClick={() => setPage("register")}
                        >
                            Register
                        </button>

                        <button
                            className="btn btn-danger"
                            onClick={logout}
                        >
                            Logout
                        </button>

                    </div>
                )}

            </nav>

            {page === "login" && (
                <Login
                    onLogin={login}
                    onRegister={() => setPage("register")}
                />
            )}

            {page === "register" && (
                <Register
                    onRegister={() => setPage("login")}
                />
            )}

            {page === "requests" && user && (
                <RequestList
                    requests={requests}
                    userRole={user.role}
                    onDelete={deleteRequest}
                    onEdit={editRequest}
                    onNew={() => setPage("new")}
                />
            )}

            {page === "new" && user && (
                <RequestForm
                    onAdd={addRequest}
                    onBack={() => setPage("requests")}
                />
            )}

            {page === "edit" && user && (
                <RequestForm
                    request={selectedRequest}
                    onUpdate={updateRequest}
                    onBack={() => setPage("requests")}
                />
            )}

        </div>
    );
}

export default App;