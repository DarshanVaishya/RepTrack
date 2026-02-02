import { useParams } from "react-router-dom";
import Container from "../utils/container";
import { useEffect, useState } from "react";
import axios from "axios";
import API_BASE_URL from "../api";
import Spinner from "../utils/Spinner";
import SessionSetEl from "../utils/SessionSetEl";
import SessionExerciseEl from "../utils/SessionExerciseEl";


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
        console.log(response.data.data)
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

  if (!session || !exercises)
    return <Spinner />

  return (
    <Container>
      <h1>Session page - {session_id}</h1>
      <p>{session.notes}</p>
      <p><span>Session Time: {formatTime(elapsed)}</span></p>
      <div>
        {exercises.map(e =>
          <SessionExerciseEl key={e.id} sessionExercise={e} session_id={session_id} workout_id={session.workout_id} />
        )}
      </div>
    </Container>
  )
}
