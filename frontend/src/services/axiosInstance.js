import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: 'https://csgis.idi.ntnu.no/api', 
});

export default axiosInstance;
