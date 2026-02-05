import axios from "axios"
import { useEffect, useState } from "react"
import API_BASE_URL from "../api"
import { useNavigate } from "react-router-dom"

export default function SessionsIndividualEl({ session }) {
  const [name, setName] = useState("")
  const navigate = useNavigate()

  useEffect(() => {
    axios.get(`${API_BASE_URL}/workout/${session.workout_id}`).then(response => {
      setName(response.data.data.name)
    })
  }, [])

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: "numeric",
      month: "long",
      day: "numeric"
    })
  }


  return (
    <div className="p-5 bg-gray-100 mb-2 cursor-pointer" onClick={() => navigate(`/sessions/${session.id}`)}>
      <p key={session.id}>{name} - {formatDate(session.started_at)}</p>
    </div>
  )
}
