package com.bah.demos.helloworld;

import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class WelcomeController {

	public static final String MESSAGE = "Hello World";

	// inject via application.properties
	@Value("${welcome.message:test}")
	private String message = MESSAGE;

	@RequestMapping("/")
	public String welcome(Map<String, Object> model) {
		model.put("message", this.message);
		return "welcome";
	}
}