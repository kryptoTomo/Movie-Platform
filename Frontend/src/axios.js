import axios from 'axios';

const instance = axios.create({
    baseURL: 'https://movie-platform-backend.onrender.com/'
});

export default instance;
