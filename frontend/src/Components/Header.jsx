import React from 'react';
import walmart from '../images/walmart.png';
import search from '../images/search.png';

const Header = () => {
  return (
    <div className='d-flex align-items-center headerMain position-relative'>
        <img src={walmart} className='ms-3' width={40} alt="" />
        <div className='searchResponsive'>
        <input className='my-2' placeholder='Search' />
        <button className='m-0 px-2' style={{ backgroundColor: 'yellowgreen' }}>
            <img src={search} width={20} alt="" />
        </button>
        </div>
        <div id='google_translate_element' className='translate-container'></div>
        <center className='ms-2'>
          <span>
            Hello, Sign in  <br/>
            <strong>Accounts & Lists</strong>
          </span>
        </center>

        <center className='ms-3'>
          <span>
            Returns<br/>
            <strong>& Orders</strong>
          </span>
        </center>
    </div>
  );
};

export default Header;
