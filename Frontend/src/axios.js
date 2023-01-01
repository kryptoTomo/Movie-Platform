import axios from 'axios';

const instance = axios.create({
    baseURL: 'movie-platform-production.up.railway.app'
});

export default instance;
