import axios from "axios"
import { useState } from "react"
import API_BASE_URL from "../api"
import { useNavigate } from "react-router-dom"
import Container from "../utils/container"
import TextInput from "../utils/TextInput"

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
    <Container>
      <div className="flex justify-center items-center min-h-screen">
        <form onSubmit={handleSubmit} className="bg-gray-100 p-5">
          <TextInput label="email" value={email} onChange={setEmail} />
          <TextInput type="password" label="password" value={password} onChange={setPassword} />
          <button type="submit">Login</button>
        </form>
      </div>
    </Container>
  )
}
