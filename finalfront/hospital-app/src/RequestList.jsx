function RequestList({
    requests,
    userRole,
    onDelete,
    onEdit,
    onNew
}) {

    const canEdit =
        userRole === "Support Engineer" ||
        userRole === "Team Lead" ||
        userRole === "Admin";

    const canDelete =
        userRole === "Admin";

    return (
        <div className="container mt-4">

            <div className="d-flex justify-content-between align-items-center mb-3">

                <h2>Requests</h2>

                <button
                    className="btn btn-primary"
                    onClick={onNew}
                >
                    New Request
                </button>

            </div>

            <div className="table-responsive">

                <table className="table table-bordered table-striped">

                    <thead className="table-dark">

                        <tr>
                            <th>Request ID</th>
                            <th>Title</th>
                            <th>Description</th>
                            <th>Department</th>
                            <th>Category</th>
                            <th>Priority</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>

                    </thead>

                    <tbody>

                        {requests.map((request) => (

                            <tr key={request.id}>

                                <td>{request.requestId}</td>

                                <td>{request.title}</td>

                                <td>{request.description}</td>

                                <td>{request.department}</td>

                                <td>{request.category}</td>

                                <td>{request.priority}</td>

                                <td>{request.status}</td>

                                <td>

                                    {canEdit && (
                                        <button
                                            className="btn btn-warning btn-sm me-2"
                                            onClick={() =>
                                                onEdit(request)
                                            }
                                        >
                                            Edit
                                        </button>
                                    )}

                                    {canDelete && (
                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() =>
                                                onDelete(request.id)
                                            }
                                        >
                                            Delete
                                        </button>
                                    )}

                                    {!canEdit && !canDelete && (
                                        <span>
                                            View only
                                        </span>
                                    )}

                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

        </div>
    );
}

export default RequestList;