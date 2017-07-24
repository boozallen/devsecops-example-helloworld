package com.bah.demos.helloworld;

import org.junit.Test;
import org.junit.Assert;

import java.util.Map;
import java.util.HashMap;

public class WelcomeControllerTest {

    @Test
    public void welcomeMessageMatchedDefault() {
        final Map<String, Object> model = new HashMap<String, Object>();
        final WelcomeController controller = new WelcomeController();
        Assert.assertEquals("welcome", controller.welcome(model));
        Assert.assertEquals(WelcomeController.MESSAGE, model.get("message"));
    }

}