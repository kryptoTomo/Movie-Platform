import axios from 'axios';

const instance = axios.create({
    baseURL: 'https://flask-app-filmmap.onrender.com/'
});

export default instance;