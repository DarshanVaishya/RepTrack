import { useParams } from "react-router-dom";
import Container from "../utils/container";
import { useEffect, useState } from "react";
import axios from "axios";
import API_BASE_URL from "../api";
import Spinner from "../utils/spinner";
import SessionExerciseEl from "../utils/SessionExerciseEl";
import PrEl from "../utils/PrEl";


export default function SessionEl() {
  const { session_id } = useParams()
  const [session, setSession] = useState(null)
  const [exercises, setExercises] = useState(null)
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/sessions/${session_id}`).then(
      response => {
        setSession(response.data.data)
        setExercises(response.data.data.session_exercises)
      })
  }, [session_id])

  useEffect(() => {
    if (!session) return
    const startTime = new Date(session.started_at).getTime();
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [session]);

  const formatTime = (totalSeconds) => {
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    return [h, m, s].map(v => String(v).padStart(2, '0')).join(':');
  };

  const handleSessionEnd = async (action) => {
    const response = await axios.post(`${API_BASE_URL}/sessions/${session_id}/${action}`)
    console.log(`Session ${action}: `, response.data.data)
  }

  if (!session || !exercises)
    return <Spinner />

  return (
    <Container>
      <h1>Session page - {session_id}</h1>
      <p>{session.notes}</p>
      <p><span>
        Session Time: {
          session.completed_at
            ? formatTime(Math.floor((new Date(session.completed_at).getTime() - new Date(session.started_at).getTime()) / 1000))
            : formatTime(elapsed)
        }
      </span></p>
      <div>
        {exercises.map(e =>
          <SessionExerciseEl key={e.id} sessionExercise={e} session_id={session_id} workout_id={session.workout_id} />
        )}
      </div>
      {session.status == "in_progress" && <div>
        <button onClick={() => handleSessionEnd("complete")}>Complete Session</button>
        <button onClick={() => handleSessionEnd("cancel")}>Cancel Session</button>
      </div>}

      {session.status == "completed" && <PrEl session_id={session_id} />}
    </Container>
  )
}
