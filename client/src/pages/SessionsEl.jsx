import { useEffect, useState } from "react";
import Container from "../utils/container";
import axios from "axios";
import API_BASE_URL from "../api";
import Spinner from "../utils/Spinner";
import SessionsIndividualEl from "../utils/SessionsIndividualEl";

export default function SessionsEl() {
  const [inprogress, setInProgress] = useState(null)
  const [completed, setCompleted] = useState(null)
  const [cancelled, setCancelled] = useState(null)

  useEffect(() => {
    axios.get(`${API_BASE_URL}/sessions?status=in_progress`).then(response => setInProgress(response.data.data))
    axios.get(`${API_BASE_URL}/sessions?status=completed`).then(response => setCompleted(response.data.data))
    axios.get(`${API_BASE_URL}/sessions?status=cancelled`).then(response => setCancelled(response.data.data))
  }, [])

  return (
    <Container>
      <h1 className="text-2xl">Sessions</h1>
      {
        !inprogress || !completed || !cancelled ? <Spinner /> :
          <div className="flex flex-col gap-5">
            <div>
              <h2>In Progress</h2>
              {inprogress.length == 0 ? <p>None</p> : inprogress.map(s => <SessionsIndividualEl key={s.id} session={s} />)}
            </div>
            <div>
              <h2>Completed</h2>
              {completed.length == 0 ? <p>None</p> : completed.map(s => <SessionsIndividualEl key={s.id} session={s} />)}
            </div>
            <div>
              <h2>Cancelled</h2>
              {cancelled.length == 0 ? <p>None</p> : cancelled.map(s => <SessionsIndividualEl key={s.id} session={s} />)}
            </div>
          </div>
      }
    </Container>
  )
}
