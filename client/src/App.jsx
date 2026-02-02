import './index.css'
import { Route, Routes } from 'react-router-dom'
import LoginEl from './pages/loginEl'
import { useEffect } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import HomeEl from './pages/homeEl';
import WorkoutEl from './pages/workoutEl';
import ExercisesEl from './pages/exercisesEl';
import SessionEl from './pages/sessionEl';

function App() {
  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      try {
        const data = jwtDecode(token);
        const currentTime = Date.now() / 1000;
        if (data.exp && data.exp < currentTime) {
          localStorage.removeItem("accessToken");
          axios.defaults.headers.common['Authorization'] = undefined;
        } else {
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }
      } catch (e) {
        console.error("Failed to decode token:", e);
        localStorage.removeItem("accessToken");
        axios.defaults.headers.common['Authorization'] = undefined;
      }
    }
  }, []);

  return (
    <Routes>
      <Route path="" element={<LoginEl />} />
      <Route path="/workouts" element={<HomeEl />} />
      <Route path="/exercises" element={<ExercisesEl />} />
      <Route path="/workouts/:workout_id" element={<WorkoutEl />} />
      <Route path="/session/:session_id" element={<SessionEl />} />
    </Routes>
  )
}

export default App
