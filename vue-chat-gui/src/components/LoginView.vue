<template>
    <div>
        <h1>Login</h1>
        <form>
            <div>
                <label for="username">Username:</label>
                <input type="text" id="username" v-model="username" placeholder="Enter username" class="input-field">
            </div>
            <div>
                <label for="password">Password:</label>
                <input type="password" id="password" v-model="password" placeholder="Enter password" class="input-field">
            </div>
            <button type="submit" @click.prevent="login">Login</button>
        </form>
    </div>
</template>

<script>
import axios from 'axios';
import jwt_decode from 'jwt-decode';


export default {
    data() {
        return {
            username: '',
            password: ''
        }
    },
    methods: {
        async login() {
            try {
                const response = await axios.post('/api/user/login', {
                    username: this.username,
                    password: this.password
                });
                console.log(response);
                localStorage.setItem('jwtToken', response.data.access_token);
                const decodedToken = jwt_decode(response.data.access_token);
                const username = decodedToken.sub;
                const expirationDate = decodedToken.exp;
                const date = new Date(expirationDate * 1000);
                localStorage.setItem('username', username);
                localStorage.setItem('expirationDate', date);
                console.log(username, expirationDate);
                // handle successful login
                this.$emit('loggedIn')
            } catch (error) {
                console.error(error);
                //pop up a toast
                // handle login error
            }
        }
    }
}
</script>

<style>
.input-field::placeholder {
    color: #999;
}
</style>