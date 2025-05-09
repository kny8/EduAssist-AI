export default function authHeader() {
    // let user = JSON.parse(localStorage.getItem('token'));

    let token =localStorage.getItem('token')

    if (token) {
        return { Authorization: 'Bearer ' + token }; // Attach token to headers
    } else {
        return {};
    }
}