// A page restored by the back button starts again from the server, not from the state it was left in.
window.addEventListener("pageshow", (event) => { if (event.persisted) location.reload(); });

// When the sign-in has expired, a request in the background is redirected to the sign-in page of
// another site, which the browser refuses. The page is then reloaded, so that the sign-in happens in
// the window itself and the person comes back here.
const sameSiteFetch = window.fetch.bind(window);
window.fetch = async (url, options = {}) => {
  let response;
  try {
    response = await sameSiteFetch(url, {...options, redirect: "manual"});
  } catch (error) {
    location.reload();
    throw error;
  }
  if (response.type === "opaqueredirect") {
    location.reload();
    throw new Error("signed out");
  }
  return response;
};
