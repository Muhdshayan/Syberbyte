import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";

export default function ActiveScreeningNotes() {
  return (
    <Card className="p-6 w-full max-w-xs rounded-lg border font-inter-regular text-left text-md">
      <div className="font-poppins-semibold text-xl mb-4">Active Screening Notes</div>
      {/* Communication Skills */}
      <div className="mb-3">
        <label className="font-medium">Communication Skills</label>
        <Select>
          <SelectTrigger className="w-full mt-1 mb-2  !bg-cream">
            <SelectValue placeholder="Select"/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="good">Good</SelectItem>
            <SelectItem value="fair">Fair</SelectItem>
            <SelectItem value="excellent">Excellent</SelectItem>
            <SelectItem value="poor">Poor</SelectItem>
          </SelectContent>
        </Select>
        <Textarea
          className="w-full text-sm"
          rows={2}
          placeholder="Notes..."
        />
      </div>
      {/* Technical Knowledge */}
      <div className="mb-3">
        <label className="font-medium">Technical Knowledge</label>
        <Select>
          <SelectTrigger className="w-full mt-1 mb-2 !bg-cream">
            <SelectValue placeholder="Rate Technical Knowledge" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="excellent">Excellent</SelectItem>
            <SelectItem value="good">Good</SelectItem>
            <SelectItem value="average">Average</SelectItem>
            <SelectItem value="poor">Poor</SelectItem>
          </SelectContent>
        </Select>
      </div>
      {/* Cultural Fit */}
      <div className="mb-3">
        <label className="font-medium">Cultural Fit</label>
        <Select>
          <SelectTrigger className="w-full mt-1 mb-2 !bg-cream">
            <SelectValue placeholder="Select a rating" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="good">Good</SelectItem>
            <SelectItem value="average">Average</SelectItem>
            <SelectItem value="not-suitable">Not suitable</SelectItem>
          </SelectContent>
        </Select>
        <Textarea
          className="w-full text-sm"
          rows={2}
          placeholder="Notes..."
        />
      </div>
      {/* Salary Expectations */}
      <div className="mb-3">
        <label className="font-medium">Salary Expectations</label>
        <Input
          className="w-full text-sm"
          placeholder="E.g 10k-35k"
        />
      </div>
      <Textarea
        className="w-full text-sm mb-3"
        rows={2}
        placeholder="Type your message here"
      />
      <div className="flex gap-2">
        <Button className="!bg-red-500 flex-1 inline-flex" >Reject</Button>
        <Button className="!bg-blue flex-1">Refer to HR</Button>
      </div>
    </Card>
  );
}