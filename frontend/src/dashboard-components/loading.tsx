import { CircularProgress } from '@mui/material';



export default function Loading() {
  return (
    <div className='flex md:flex-row flex-col justify-center items-center gap-2 w-full min-h-[calc(100vh-200px)]'>
      <CircularProgress 
        size={40} 
        className='text-blue z-5'/>
        <p className='text-lg font-poppins-semibold'>
          Loading...
        </p>
    </div>
  );
}