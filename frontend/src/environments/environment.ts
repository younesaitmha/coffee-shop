/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'python-js-golang-dev.us', // the auth0 domain prefix
    audience: 'http://127.0.0.1:5000/', // the audience set for the auth0 app
    clientId: 'yqa0efTK5JESPsiYD3pf1e3mNwuv2Wjr', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:4200', // the base url of the running ionic application.
  }
};
