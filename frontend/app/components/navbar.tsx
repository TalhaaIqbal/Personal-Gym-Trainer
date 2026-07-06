'use client'

export default function Navbar() {
  return (
    <>
      <nav className="fixed w-full z-20 top-0 start-0 bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 backdrop-blur-md border-b border-blue-700/50 shadow-lg">
        <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
          <a href="https://GymTime.com/" className="flex items-center space-x-3 rtl:space-x-reverse group">
            {/* <Image src="https://GymTime.com/docs/images/logo.svg" className="h-7" alt="GymTime Logo" width={32} height={32} /> */}
            <span className="self-center text-2xl font-bold text-white whitespace-nowrap group-hover:text-blue-200 transition-colors duration-300">GymTime</span>
          </a>
          <div className="flex items-center md:order-2 space-x-3 md:space-x-0 rtl:space-x-reverse">
            <button type="button" className="flex text-sm bg-blue-700/50 rounded-full md:me-0 focus:ring-4 focus:ring-blue-500/50 hover:bg-blue-600/50 transition-all duration-300" id="user-menu-button" aria-expanded="false" data-dropdown-toggle="user-dropdown" data-dropdown-placement="bottom">
              <span className="sr-only">Open user menu</span>
              {/* <Image className="w-8 h-8 rounded-full" src="/docs/images/people/profile-picture-5.jpg" alt="user photo" width={32} height={32} /> */}
            </button>
            <div className="z-50 hidden bg-blue-900/95 backdrop-blur-md border border-blue-600/50 rounded-xl shadow-2xl w-44" id="user-dropdown">
              <div className="px-4 py-3 text-sm border-b border-blue-700/50">
                <span className="block text-white font-medium">Joseph McFall</span>
                <span className="block text-blue-200 truncate">name@GymTime.com</span>
              </div>
              <ul className="p-2 text-sm text-blue-100 font-medium" aria-labelledby="user-menu-button">
                <li>
                  <a href="#" className="inline-flex items-center w-full p-2 hover:bg-blue-700/50 hover:text-white rounded-lg transition-all duration-200">Dashboard</a>
                </li>
                <li>
                  <a href="#" className="inline-flex items-center w-full p-2 hover:bg-blue-700/50 hover:text-white rounded-lg transition-all duration-200">Settings</a>
                </li>
                <li>
                  <a href="#" className="inline-flex items-center w-full p-2 hover:bg-blue-700/50 hover:text-white rounded-lg transition-all duration-200">Earnings</a>
                </li>
                <li>
                  <a href="#" className="inline-flex items-center w-full p-2 hover:bg-blue-700/50 hover:text-white rounded-lg transition-all duration-200">Sign out</a>
                </li>
              </ul>
            </div>
            <button data-collapse-toggle="navbar-user" type="button" className="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-blue-100 rounded-lg md:hidden hover:bg-blue-700/50 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all duration-300" aria-controls="navbar-user" aria-expanded="false">
              <span className="sr-only">Open main menu</span>
              <svg className="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" strokeLinecap="round" strokeWidth="2" d="M5 7h14M5 12h14M5 17h14" /></svg>
            </button>
          </div>
          <div className="items-center justify-between hidden w-full md:flex md:w-auto md:order-1" id="navbar-user">
            <ul className="font-medium flex flex-col p-4 md:p-0 mt-4 border border-blue-700/50 rounded-xl bg-blue-800/50 backdrop-blur-md md:flex-row md:space-x-1 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-transparent">
              <li>
                <a href="#" className="block py-2 px-4 text-white bg-blue-600/50 rounded-lg md:bg-blue-600/30 md:hover:bg-blue-500/50 md:px-4 md:py-2 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/25" aria-current="page">Home</a>
              </li>
              <li>
                <a href="#" className="block py-2 px-4 text-blue-100 rounded-lg hover:bg-blue-700/50 hover:text-white md:hover:bg-blue-700/30 md:px-4 md:py-2 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/25">About</a>
              </li>
              <li>
                <a href="#" className="block py-2 px-4 text-blue-100 rounded-lg hover:bg-blue-700/50 hover:text-white md:hover:bg-blue-700/30 md:px-4 md:py-2 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/25">Services</a>
              </li>
              <li>
                <a href="#" className="block py-2 px-4 text-blue-100 rounded-lg hover:bg-blue-700/50 hover:text-white md:hover:bg-blue-700/30 md:px-4 md:py-2 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/25">Pricing</a>
              </li>
              <li>
                <a href="#" className="block py-2 px-4 text-blue-100 rounded-lg hover:bg-blue-700/50 hover:text-white md:hover:bg-blue-700/30 md:px-4 md:py-2 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/25">Contact</a>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </>
  )
}