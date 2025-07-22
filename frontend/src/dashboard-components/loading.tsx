import { CircularProgress } from '@mui/material';



export default function Loading() {
  return (
    <div className='flex md:flex-row flex-col justify-center items-center gap-2 h-screen'>
      <CircularProgress 
        size={40} 
        className='text-blue'/>
        <p className='text-lg font-poppins-semibold'>
          Loading...
        </p>
    </div>
  );
}