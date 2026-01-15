import axios from "axios"
import { useState } from "react"
import API_BASE_URL from "../api"
import { useNavigate } from "react-router-dom"

export default function LoginEl() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    const params = new URLSearchParams();
    params.append("username", email);
    params.append("password", password);
    const response = await axios.post(`${API_BASE_URL}/users/login`, params)
    const token = response.data.access_token
    localStorage.setItem("accessToken", token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    navigate("/workouts")
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Email</label>
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
      </div>

      <div>
        <label>Password</label>
        <input type="text" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
      </div>

      <button type="submit">Login</button>
    </form>
  )
}
