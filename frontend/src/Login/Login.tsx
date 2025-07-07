import {
  Card,

  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import useLogin from "./useLogin";
import CircularProgress from '@mui/material/CircularProgress';


export default function Login () {
        const {
          email,
          setEmail,
          password,
          setPassword,
          loading,
          error,
          selectedRole,
          setSelectedRole,
          handleSubmit,
        } = useLogin("HR");
    const roles = ["HR", "Recruiter", "Admin"] as const;
    return (
       <div className="flex md:flex-row flex-col justify-center items-start md:h-screen h-[800px] w-full">
          <img
              src="/pexels-olga-neptuna-1090543-2078774.jpg"
              alt="background"
              className="absolute inset-0 md:h-full h-[800px] w-full object-cover"
            />
            <div className="absolute inset-0 md:h-full h-[800px] bg-gradient-to-tl from-blue via-green to-green mix-blend-multiply"></div>
          <div className="flex flex-col md:w-[50%] w-full md:h-[60%] h-[45%] items-start p-5 justify-between z-3">
            <img
                src="/star.svg"
                className="w-5 h-5"
            />
            <div className="w-full flex flex-col items-center justify-center mt-5 ">
                <div className="md:w-[50%] w-full text-center justify-center text-white md:text-5xl text-4xl font-semibold font-['Poppins'] md:leading-[60px]  tracking-[-0.40px] leading-10">Welcome to SmartRecruit</div>
                <div className="text-xl w-[80%] text-white font-inter-regular leading-[36.8px]">Your AI-powered hiring assistant.</div>
            </div>
          </div>
          <div className=" flex flex-col md:w-[50%]  w-full items-center justify-center h-full z-3 md:pt-0 pt-5">
            <div className="flex flex-col md:items-start items-center justify-center">
                <div className="w-auto p-2 bg-cream flex flex-row rounded-md font-inter-medium text-slate-700">
                    {roles.map((role)=>(
                        <div
                            key={role}
                            className={`cursor-pointer p-1 px-3 rounded-sm transition-colors duration-300 ${
                                selectedRole === role
                                    ? "bg-white text-slate-900"
                                    : " text-slate-700"
                            }`}
                            onClick={() => setSelectedRole(role)}
                        >
                            {role}
                        </div>
                    ))}
                </div>
                 <Card className=" md:w-[400px] w-full h-auto font-inter-regular mt-2">
                    <CardHeader className="">
                      <CardTitle className="md:text-left text-center font-poppins-semibold text-3xl">Login to your account</CardTitle>
                      <h2 className="md:text-left text-center mt-3">Login to Continue</h2>
                      <CardDescription className="text-left text-sm font-inter-regular mt-3">
                        Enter your email and Password
                      </CardDescription>
                    </CardHeader>
                    <form onSubmit={handleSubmit}>
                    <CardContent>
                      
                        <div className="flex flex-col gap-6">
                          <div className="grid gap-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                              id="email"
                              type="email"
                              placeholder="m@example.com"
                              value={email}
                              onChange={e => setEmail(e.target.value)}
                              required
                            />
                          </div>
                          <div className="grid gap-2">
                            <div className="flex items-center">
                              <Label htmlFor="password">Password</Label>
                            </div>
                            <Input 
                            id="password" 
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)} 
                            required />
                          </div>
                          {error && (
                                        <div className="text-red-500 text-sm">{error}</div>
                           )}
                        </div>
                      
                    </CardContent>
                    <CardFooter className="flex-col gap-2 md:mt-4 mt-6">
                      <Button
                        type="submit"
                        disabled={loading}
                        className="w-full !bg-[var(--color-blue)] text-white flex items-center justify-center"
                      >
                        {loading ? <CircularProgress size={20} color="inherit" /> : "Login"}
                      </Button>
                    </CardFooter>
                    </form>
                  </Card>
                </div>
            </div>
        </div>

    );
};
