import { useState } from 'react';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/upload/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setStatus(data.detail || "Upload complete");
    } catch (err) {
      setStatus("Upload failed");
    }
  };

  return (
    <div style={{ marginBottom: "20px", textAlign: "center" }}>
      <input type="file" accept=".txt" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} style={{ marginLeft: "10px" }}>Upload</button>
      <p>{status}</p>
    </div>
  );
}

export default FileUpload;
